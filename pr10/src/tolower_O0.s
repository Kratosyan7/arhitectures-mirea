	.file	"tolower.c"
	.option pic
	.attribute arch, "rv64i2p1_m2p0_a2p1_f2p2_d2p2_c2p0_zicsr2p0_zifencei2p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
	.text
	.align	1
	.globl	my_tolower
	.type	my_tolower, @function
my_tolower:
.LFB0:
	.cfi_startproc
	addi	sp,sp,-48
	.cfi_def_cfa_offset 48
	sd	s0,40(sp)
	.cfi_offset 8, -8
	addi	s0,sp,48
	.cfi_def_cfa 8, 0
	sd	a0,-40(s0)
	sd	a1,-48(s0)
	ld	a5,-48(s0)
	sd	a5,-24(s0)
.L3:
	ld	a5,-40(s0)
	lbu	a5,0(a5)
	sb	a5,-25(s0)
	lbu	a5,-25(s0)
	andi	a4,a5,0xff
	li	a5,64
	bleu	a4,a5,.L2
	lbu	a5,-25(s0)
	andi	a4,a5,0xff
	li	a5,90
	bgtu	a4,a5,.L2
	lbu	a5,-25(s0)
	addiw	a5,a5,32
	sb	a5,-25(s0)
.L2:
	ld	a5,-48(s0)
	addi	a4,a5,1
	sd	a4,-48(s0)
	lbu	a4,-25(s0)
	sb	a4,0(a5)
	ld	a5,-40(s0)
	addi	a5,a5,1
	sd	a5,-40(s0)
	lbu	a5,-25(s0)
	andi	a5,a5,0xff
	bne	a5,zero,.L3
	ld	a4,-48(s0)
	ld	a5,-24(s0)
	sub	a5,a4,a5
	sext.w	a5,a5
	mv	a0,a5
	ld	s0,40(sp)
	.cfi_restore 8
	.cfi_def_cfa 2, 48
	addi	sp,sp,48
	.cfi_def_cfa_offset 0
	jr	ra
	.cfi_endproc
.LFE0:
	.size	my_tolower, .-my_tolower
	.globl	tstStr
	.section	.rodata
	.align	3
.LC0:
	.string	"Hello World!"
	.section	.data.rel.local,"aw"
	.align	3
	.type	tstStr, @object
	.size	tstStr, 8
tstStr:
	.dword	.LC0
	.globl	outStr
	.bss
	.align	3
	.type	outStr, @object
	.size	outStr, 64
outStr:
	.zero	64
	.section	.rodata
	.align	3
.LC1:
	.string	"Input:  %s\nOutput: %s\n"
	.text
	.align	1
	.globl	main
	.type	main, @function
main:
.LFB1:
	.cfi_startproc
	addi	sp,sp,-16
	.cfi_def_cfa_offset 16
	sd	ra,8(sp)
	sd	s0,0(sp)
	.cfi_offset 1, -8
	.cfi_offset 8, -16
	addi	s0,sp,16
	.cfi_def_cfa 8, 0
	lla	a5,tstStr
	ld	a5,0(a5)
	lla	a1,outStr
	mv	a0,a5
	call	my_tolower
	lla	a5,tstStr
	ld	a5,0(a5)
	lla	a2,outStr
	mv	a1,a5
	lla	a0,.LC1
	call	printf@plt
	li	a5,0
	mv	a0,a5
	ld	ra,8(sp)
	.cfi_restore 1
	ld	s0,0(sp)
	.cfi_restore 8
	.cfi_def_cfa 2, 16
	addi	sp,sp,16
	.cfi_def_cfa_offset 0
	jr	ra
	.cfi_endproc
.LFE1:
	.size	main, .-main
	.ident	"GCC: (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0"
	.section	.note.GNU-stack,"",@progbits
